import hypothesis.startegies as st
from sympy import (
    Symbol, Integer, Float, Expr, Add, Mul, Pow, Piecewise, Derivative)

@st.composite
def symbols(draw, *args, **kwargs) -> Symbol:
    kwargs.setdefault('alphabet',
                      st.characters(whitelist_categories=('L', 'N', 'Zs')))
    name = (draw(st.characters(whitelist_categories=('L',))) +
            draw(st.text(*args, **kwargs)))
    real = draw(st.bools())
    return Symbol(name, real=real)

@st.composite
def expressions(draw, min_value: float = float('-inf'),
                max_value: float = float('inf')) -> Expr:
    ...
    # symbols = draw(st.lists(nutrients()))
    # constructor, arg_pattern = draw(st.sampled_from(OPTIONS))
    # args: List = []
    # for arg in arg_pattern:
    #     if arg == Arg.SYMBOL:
    #         value = draw(st.sampled_from(symbols))
    #     elif arg == Arg.EXPR:
    #         value = draw(expressions(min_value, max_value))
    #     elif arg == Arg.BINOP:
    #         value = draw(st.sampled_from(BINOPS))
    #     elif arg == Arg.ATOM:
    #         value = draw(st.one_of(
    #             st.sampled_from(symbols),
    #             st.integers(min_value=min_value, max_value=max_value),
    #             st.floats(min_value=min_value, max_value=max_value)))
    #     else:
    #         raise(ValueError(f"Unknown enum value: {arg}"))
    #     args.append(value)
    # return constructor(*args)


st.register_type_strategy(Integer, st.builds(Integer, st.integers()))
st.register_type_strategy(Float, st.builds(Float, st.floats()))
st.register_type_strategy(
    Add, st.builds(lambda args: Add(*args), st.lists(expressions())))
st.register_type_strategy(
    Mul, st.builds(lambda args: Mul(*args), st.lists(expressions())))
st.register_type_strategy(Pow, st.builds(Pow, expressions(), expressions()))
st.register_type_strategy(Piecewise, piecewises())
st.register_type_strategy(
    Derivative, st.builds(Derivative, expressions(), symbols()))
st.register_type_strategy(Expr, expressions())
